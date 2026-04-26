这份 Markdown 文档深入解析了 xv6 中 `sleep` 与 `wakeup` 的协作机制，以及它是如何通过锁管理来实现原子性的进程切换。

---

# xv6 进程休眠与调度深度解析

## 1. 核心设计理念
在多处理器系统中，`sleep` 的本质是**原子性地让出 CPU**。为了防止“错过唤醒”（Lost Wakeup），`sleep` 必须在释放等待条件的锁之前，先获取进程控制块的锁。

---

## 2. 系统调用流程
从用户态到内核态的调用链如下：
1. **用户态**: `sleep(n)` (用户程序调用)
2. **陷阱层**: `usertrap()` -> `syscall()`
3. **内核函数**: `sys_sleep()`
   - 获取 `tickslock`。
   - 检查当前 `ticks`。
   - 循环调用内核 `sleep(&ticks, &tickslock)`。

---

## 3. sleep 函数实现 (kernel/proc.c)

```c
void sleep(void *chan, struct spinlock *lk) {
  struct proc *p = myproc();
  
  // 必须先持有 p->lock 才能改变进程状态
  // 同时也为了保证在释放 lk 后，没有其他的 wakeup 能错过这个进程
  acquire(&p->lock); 
  release(lk);       // 释放外部锁（如 tickslock）

  // 设置休眠通道和状态
  p->chan = chan;
  p->state = SLEEPING;

  sched();           // 核心：切换到调度器执行

  // 被唤醒后从这里继续执行
  p->chan = 0;
  release(&p->lock);
  acquire(lk);       // 重新持有进入 sleep 前的锁
}
```

---

## 4. 关键：如何避免“错过唤醒”？
假设我们没有 `p->lock` 保护：
1. **CPU 0 (Sleep)**: 检查 `ticks` 发现没到时间，准备睡。
2. **CPU 1 (Interrupt)**: 时钟中断发生，调用 `wakeup(&ticks)`。但此时 CPU 0 的进程状态还是 `RUNNING`。
3. **CPU 0 (Sleep)**: 将状态设为 `SLEEPING`。
4. **结果**: 进程错过了唤醒信号，可能永远睡死。

**xv6 解决方案**：
通过要求 `sleep` 调用者持有 `lk`，并在 `sleep` 内部先拿 `p->lock` 再放 `lk`。这样 `wakeup` 在尝试获取 `p->lock` 时会被阻塞，直到 `sleep` 完成状态设置并进入调度。

---

## 5. 调度器接管 (The Scheduler)

当 `sleep` 调用 `sched()` 时，最终会进入 `swtch`：
* **swtch**: 保存当前内核线程上下文，恢复 `cpu->context`（即调度器线程）。
* **scheduler() 循环**:
    ```c
    for(;;){
      for(p = proc; p < &proc[NPROC]; p++) {
        acquire(&p->lock);
        if(p->state == RUNNABLE) {
          p->state = RUNNING;
          c->proc = p;
          swtch(&c->context, &p->context); // 切换到新进程
          c->proc = 0;
        }
        release(&p->lock);
      }
    }
    ```

---

## 6. 唤醒机制 (wakeup)

当条件满足（如时钟中断 `ticks++`）时，内核调用 `wakeup(chan)`：

```c
void wakeup(void *chan) {
  struct proc *p;
  for(p = proc; p < &proc[NPROC]; p++) {
    if(p != myproc()){
      acquire(&p->lock);
      if(p->state == SLEEPING && p->chan == chan) {
        p->state = RUNNABLE; // 仅仅是改状态，不负责切换
      }
      release(&p->lock);
    }
  }
}
```

---

## 7. 总结：状态机转换图



* **RUNNING → SLEEPING**: 进程在 `sleep()` 中通过 `sched()` 主动放弃 CPU。
* **SLEEPING → RUNNABLE**: 另一个线程或中断处理程序调用 `wakeup()`，将进程标记为可运行。
* **RUNNABLE → RUNNING**: `scheduler()` 循环扫描到该进程，通过 `swtch` 恢复运行。
