---
layout: lecture
title: "6.s081 Lab1 Syscall"
date: 2026-03-16
ready: true
sync: true
syncdate: 2026-03-16
---

## Lab1-1

```
用户程序 → ecall指令 → 内核syscall()函数 → 具体系统调用函数 → 返回用户程序
```

- **a7**: 系统调用号
- **a0-a6**: 系统调用参数
- **a0**: 返回值

核心组件:

```c
/* 用户空间接口 */

// user/user.h
int trace(int mask);

// user/usys.pl - 生成系统调用存根
entry("trace");  // 生成: li a7, SYS_trace; ecall; ret
```

```c
/* 内核系统调用表 */

// kernel/syscall.h
#define SYS_trace  22

// kernel/syscall.c  
static uint64 (*syscalls[])(void) = {
    [SYS_trace]   sys_trace,
    // ... 其他系统调用
};
```

```c
// 进程结构扩展

// kernel/proc.h
struct proc {
    // ... 其他字段
    int trace_mask;  // 跟踪掩码 - 新增字段
};
```

## 实现步骤

sys_trace 函数
```c
// kernel/sysproc.c
uint64 sys_trace(void) {
    int mask;
    if(argint(0, &mask) < 0)  // 从用户空间获取mask参数
        return -1;
    
    struct proc *p = myproc();
    p->trace_mask = mask;     // 设置进程的跟踪掩码
    return 0;
}
```

fork 继承
```c
// kernel/proc.c - fork()函数中
np->trace_mask = p->trace_mask;  // 子进程继承父进程的trace_mask
```

系统调用跟踪
```c
// kernel/syscall.c
void syscall(void) {
    int num = p->trapframe->a7;  // 获取系统调用号
    
    if(num > 0 && num < NELEM(syscalls) && syscalls[num]) {
        p->trapframe->a0 = syscalls[num]();  // 执行系统调用
        
        // 关键：检查是否需要跟踪
        if (p->trace_mask & (1 << num)) {
            printf("%d: syscall %s -> %d\n", 
                   p->pid, syscall_names[num], p->trapframe->a0);
        }
    }
}
```


## 完整执行流程

`sysproc.c->syctrace()`
1. 用户程序调用 trace(32)
2. 通过 usys.S 存根进入内核
3. syscall()调用 sys_trace()
4. sys_trace() 设置当前进程 trace_mask = 32
5. 返回用户程序

`syscall.c->syscall()`
1. 用户程序调用read()
2. 通过ecall进入内核syscall()
3. syscall()执行read()系统调用
4. 检查: if (32 & (1 << 5)) == true
5. 打印: "3: syscall read -> 1023"
6. 返回用户程序

