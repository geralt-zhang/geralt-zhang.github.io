---
layout: lecture
title: "mit6.s081 labs"
details:
date: 2025-10-23
ready: true
sync: true
syncdate: 2025-10-23
---

## GDB 的使用

* 它现在卡在哪？（用 bt）
* 它在执行哪一行？（用 info line, list）
* 它在用哪些数据？（info locals, p var）
* 为什么它走到这里？（条件断点、watch）
* 我能重现吗？（run < input）
* 如果我改变量呢？（set var = xxx)

Some things you’ll do in 6.S081

1. You will build a driver for a network stack that
sends packets over the real Internet
2. You will redesign a memory allocator so that it
can scale across multiple cores
3. You will implement fork and make it efficient
through an optimization called copy-on-write

User <-> kernel interface

• Primarily system calls
• Examples:
fd = open(“out”, 1);
len = write(fd, “hello\n”, 6);
pid = fork();
• Look and behave like function calls, but they aren’t

| System Call | Description |
|--------------|-------------|
| int fork(void) | Create a process, return child's PID. |
| int exit(int status) | Terminate the current process; status reported to wait(). No return. |
| int wait(int *status) | Wait for a child to exit; exit status in *status; returns child PID. |
| int kill(int pid) | Terminate process pid. Returns 0, or -1 for error. |
| int getpid(void) | Return the current process's PID. |
| int sleep(int n) | Pause for n clock ticks. |
| int exec(char *file, char *argv[]) | Load a file and execute it with arguments; only returns if error. |
| char *sbrk(int n) | Grow process's memory by n bytes. Returns start of new memory. |
| int open(char *file, int flags) | Open a file; flags indicate read/write; returns a file descriptor (fd). |
| int write(int fd, char *buf, int n) | Write n bytes from buf to file descriptor fd; returns n. |
| int read(int fd, char *buf, int n) | Read n bytes into buf; returns number read; or 0 if end of file. |
| int close(int fd) | Release open file descriptor fd. |
| int dup(int fd) | Return a new file descriptor referring to the same file as fd. |
| int pipe(int p[]) | Create a pipe; put read/write file descriptors in p[0] and p[1]. |
| int chdir(char *dir) | Change the current directory. |
| int mkdir(char *dir) | Create a new directory. |
| int mknod(char *file, int major, int minor) | Create a device file. |
| int fstat(int fd, struct stat *st) | Place info about an open file into *st. |
| int stat(char *file, struct stat *st) | Place info about a named file into *st. |
| int link(char *file1, char *file2) | Create another name (file2) for the file file1. |
| int unlink(char *file) | Remove a file. |


