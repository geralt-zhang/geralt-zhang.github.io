---
layout: lecture
title: "NVMe Virt"
details: PCIe & NVme detail
date: 2025-9-27
ready: true
sync: true
syncdate: 2025-09-27
---

什么是 `nvme-virt` ？

通过虚拟出的 PCIe 设备，模拟 NVMe SSD 的使用

代码结构：

The device is emulated at the PCI layer, presenting a native NVMe device to the entire system. Thus, NVMeVirt has the capability not only to function as a standard storage device, but also to be utilized in advanced storage configurations, such as NVMe-oF target offloading, kernel bypassing, and PCI peer-to-peer communication.
