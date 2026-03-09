## GitHub Copilot Chat

- Extension: 0.38.2 (prod)
- VS Code: 1.110.1 (61b3d0ab13be7dda2389f1d3e60a119c7f660cc3)
- OS: linux 6.12.47+rpt-rpi-2712 arm64
- Remote Name: ssh-remote
- Extension Kind: Workspace
- GitHub Account: Isuru67

## Network

User Settings:
```json
  "http.systemCertificatesNode": true,
  "github.copilot.advanced.debug.useElectronFetcher": true,
  "github.copilot.advanced.debug.useNodeFetcher": false,
  "github.copilot.advanced.debug.useNodeFetchFetcher": true
```

Connecting to https://api.github.com:
- DNS ipv4 Lookup: Error (49 ms): getaddrinfo EAI_AGAIN api.github.com
- DNS ipv6 Lookup: Error (1 ms): getaddrinfo EAI_AGAIN api.github.com
- Proxy URL: None (0 ms)
- Electron fetch: Unavailable
- Node.js https: Error (39 ms): Error: getaddrinfo EAI_AGAIN api.github.com
	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)
- Node.js fetch (configured): Error (50 ms): TypeError: fetch failed
	at node:internal/deps/undici/undici:14902:13
	at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
	at async n._fetch (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5001:4900)
	at async n.fetch (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5001:4212)
	at async d (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5033:190)
	at async Jm._executeContributedCommand (file:///home/isuru/.vscode-server/cli/servers/Stable-61b3d0ab13be7dda2389f1d3e60a119c7f660cc3/server/out/vs/workbench/api/node/extensionHostProcess.js:494:48672)
  Error: getaddrinfo EAI_AGAIN api.github.com
  	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)

Connecting to https://api.githubcopilot.com/_ping:
- DNS ipv4 Lookup: Error (0 ms): getaddrinfo EAI_AGAIN api.githubcopilot.com
- DNS ipv6 Lookup: Error (1 ms): getaddrinfo EAI_AGAIN api.githubcopilot.com
- Proxy URL: None (0 ms)
- Electron fetch: Unavailable
- Node.js https: Error (39 ms): Error: getaddrinfo EAI_AGAIN api.githubcopilot.com
	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)
- Node.js fetch (configured): Error (50 ms): TypeError: fetch failed
	at node:internal/deps/undici/undici:14902:13
	at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
	at async n._fetch (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5001:4900)
	at async n.fetch (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5001:4212)
	at async d (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5033:190)
	at async Jm._executeContributedCommand (file:///home/isuru/.vscode-server/cli/servers/Stable-61b3d0ab13be7dda2389f1d3e60a119c7f660cc3/server/out/vs/workbench/api/node/extensionHostProcess.js:494:48672)
  Error: getaddrinfo EAI_AGAIN api.githubcopilot.com
  	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)

Connecting to https://copilot-proxy.githubusercontent.com/_ping:
- DNS ipv4 Lookup: Error (0 ms): getaddrinfo EAI_AGAIN copilot-proxy.githubusercontent.com
- DNS ipv6 Lookup: Error (0 ms): getaddrinfo EAI_AGAIN copilot-proxy.githubusercontent.com
- Proxy URL: None (1 ms)
- Electron fetch: Unavailable
- Node.js https: Error (39 ms): Error: getaddrinfo EAI_AGAIN copilot-proxy.githubusercontent.com
	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)
- Node.js fetch (configured): Error (50 ms): TypeError: fetch failed
	at node:internal/deps/undici/undici:14902:13
	at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
	at async n._fetch (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5001:4900)
	at async n.fetch (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5001:4212)
	at async d (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5033:190)
	at async Jm._executeContributedCommand (file:///home/isuru/.vscode-server/cli/servers/Stable-61b3d0ab13be7dda2389f1d3e60a119c7f660cc3/server/out/vs/workbench/api/node/extensionHostProcess.js:494:48672)
  Error: getaddrinfo EAI_AGAIN copilot-proxy.githubusercontent.com
  	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)

Connecting to https://mobile.events.data.microsoft.com: Error (50 ms): TypeError: fetch failed
	at node:internal/deps/undici/undici:14902:13
	at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
	at async n._fetch (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5001:4900)
	at async n.fetch (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5001:4212)
	at async d (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5038:136)
	at async Jm._executeContributedCommand (file:///home/isuru/.vscode-server/cli/servers/Stable-61b3d0ab13be7dda2389f1d3e60a119c7f660cc3/server/out/vs/workbench/api/node/extensionHostProcess.js:494:48672)
  Error: getaddrinfo EAI_AGAIN mobile.events.data.microsoft.com
  	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)
Connecting to https://dc.services.visualstudio.com: Error (50 ms): TypeError: fetch failed
	at node:internal/deps/undici/undici:14902:13
	at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
	at async n._fetch (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5001:4900)
	at async n.fetch (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5001:4212)
	at async d (/home/isuru/.vscode-server/extensions/github.copilot-chat-0.38.2/dist/extension.js:5038:136)
	at async Jm._executeContributedCommand (file:///home/isuru/.vscode-server/cli/servers/Stable-61b3d0ab13be7dda2389f1d3e60a119c7f660cc3/server/out/vs/workbench/api/node/extensionHostProcess.js:494:48672)
  Error: getaddrinfo EAI_AGAIN dc.services.visualstudio.com
  	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)
Connecting to https://copilot-telemetry.githubusercontent.com/_ping: Error (39 ms): Error: getaddrinfo EAI_AGAIN copilot-telemetry.githubusercontent.com
	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)
Connecting to https://copilot-telemetry.githubusercontent.com/_ping: Error (39 ms): Error: getaddrinfo EAI_AGAIN copilot-telemetry.githubusercontent.com
	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)
Connecting to https://default.exp-tas.com: Error (40 ms): Error: getaddrinfo EAI_AGAIN default.exp-tas.com
	at GetAddrInfoReqWrap.onlookupall [as oncomplete] (node:dns:122:26)

Number of system certificates: 416

## Documentation

In corporate networks: [Troubleshooting firewall settings for GitHub Copilot](https://docs.github.com/en/copilot/troubleshooting-github-copilot/troubleshooting-firewall-settings-for-github-copilot).