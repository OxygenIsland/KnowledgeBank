#!/usr/bin/env node

/**
 * 简单的测试 Agent Skill - Hello World
 * 这是一个基础的 MCP 服务器示例
 */

const readline = require('readline');

// 创建标准输入输出接口
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// MCP 协议消息处理
rl.on('line', (line) => {
  try {
    const request = JSON.parse(line);
    
    // 处理初始化请求
    if (request.method === 'initialize') {
      const response = {
        jsonrpc: '2.0',
        id: request.id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: {
            tools: {}
          },
          serverInfo: {
            name: 'hello-world-skill',
            version: '1.0.0'
          }
        }
      };
      console.log(JSON.stringify(response));
    }
    
    // 处理工具列表请求
    else if (request.method === 'tools/list') {
      const response = {
        jsonrpc: '2.0',
        id: request.id,
        result: {
          tools: [
            {
              name: 'sayHello',
              description: '向指定的人打招呼',
              inputSchema: {
                type: 'object',
                properties: {
                  name: {
                    type: 'string',
                    description: '要打招呼的人的名字'
                  }
                },
                required: ['name']
              }
            },
            {
              name: 'getCurrentTime',
              description: '获取当前时间',
              inputSchema: {
                type: 'object',
                properties: {}
              }
            }
          ]
        }
      };
      console.log(JSON.stringify(response));
    }
    
    // 处理工具调用
    else if (request.method === 'tools/call') {
      const toolName = request.params.name;
      const args = request.params.arguments || {};
      
      let result;
      
      if (toolName === 'sayHello') {
        const name = args.name || 'World';
        result = {
          content: [
            {
              type: 'text',
              text: `你好，${name}！欢迎使用自定义 Agent Skills！🎉`
            }
          ]
        };
      } else if (toolName === 'getCurrentTime') {
        const now = new Date();
        result = {
          content: [
            {
              type: 'text',
              text: `当前时间：${now.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}`
            }
          ]
        };
      } else {
        result = {
          content: [
            {
              type: 'text',
              text: `未知工具：${toolName}`
            }
          ],
          isError: true
        };
      }
      
      const response = {
        jsonrpc: '2.0',
        id: request.id,
        result: result
      };
      console.log(JSON.stringify(response));
    }
    
    // 处理 initialized 通知
    else if (request.method === 'notifications/initialized') {
      // 不需要响应
    }
    
  } catch (error) {
    const errorResponse = {
      jsonrpc: '2.0',
      id: request.id || null,
      error: {
        code: -32603,
        message: error.message
      }
    };
    console.error(JSON.stringify(errorResponse));
  }
});

// 错误处理
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  process.exit(1);
});
