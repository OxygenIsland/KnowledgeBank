---
title: "[[Graphics performance fundamentals]]"
type: Reference
status: todo
Creation Date: 2025-04-23 15:50
tags:
---
This page contains some simple guidelines for optimzing rendering performance in your application.

## Before you begin: locate and understand the problem

Before you make any changes, you must profile(剖析) your application to identify the cause of the problem. If you attempt to solve a performance problem before you understand its cause, you might waste your time or make the problem worse. Additionally, rendering-related performance problems can occur on the CPU or the GPU. Strategies(策略) for fixing these problems are quite different, so it’s important to understand where your problem is before taking any action.

The following article on the Unity Learn site is a comprehensive(全面的) introduction to graphics performance, and contains information on identifying and fixing problems: [Fixing performance problems](https://learn.unity.com/tutorial/fixing-performance-problems-2019-3). If you are not yet familiar with this subject, read the article before following any of the advice on this page.

## Reducing the CPU cost of rendering

Usually, the greatest contributor to CPU rendering time is the cost of sending rendering commands to the GPU. Rendering commands include draw calls (commands to draw geometry), and commands to change the settings on the GPU before drawing the geometry. If this is the case, consider these options: