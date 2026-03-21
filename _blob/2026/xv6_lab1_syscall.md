---
layout: lecture
title: "6.s081 lab1 syscall"
date: 2026-03-16
ready: true
sync: true
syncdate: 2026-03-16
---

## lab1.1: add trace for syscall()

```
用户程序 → ecall指令 → 内核syscall()函数 → 具体系统调用函数 → 返回用户程序
```

- **a7**: 系统调用号
- **a0-a6**: 系统调用参数
- **a0**: 返回值

核心组件:

```c
/* User space interface */

// user/user.h
int trace(int mask);

// user/usys.pl - Generate syscall stub
entry("trace");  // Generate: li a7, SYS_trace; ecall; ret
```

```c
/* Kernel syscall table */

// kernel/syscall.h
#define SYS_trace  22

// kernel/syscall.c  
static uint64 (*syscalls[])(void) = {
    [SYS_trace]   sys_trace,
    // ... other syscall
};
```

```c
// Process structure extension

// kernel/proc.h
struct proc {
    // ... other parameters
    int trace_mask;  // Trace mask - new field
};
```

## 实现步骤

sys_trace 函数
```c
// kernel/sysproc.c
uint64 sys_trace(void) {
    int mask;
    if(argint(0, &mask) < 0)  // Get mask parameter from user space
        return -1;
    
    struct proc *p = myproc();
    p->trace_mask = mask;     // Set process trace mask
    return 0;
}
```

fork 继承
```c
// kernel/proc.c - fork()函数中
np->trace_mask = p->trace_mask;  // Child process inherits parent's trace_mask
```

系统调用跟踪
```c
// kernel/syscall.c
void syscall(void) {
    int num = p->trapframe->a7;  // Get syscall number
    
    if(num > 0 && num < NELEM(syscalls) && syscalls[num]) {
        p->trapframe->a0 = syscalls[num]();  // Execute syscall
        
        // Key: check if tracing is needed
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

