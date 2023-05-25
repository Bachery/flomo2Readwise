# flomo2Readwise
Sync flomo memos from Notion database to Readwise by GitHub Action.

通过 GitHub Action，自动将 flomo 笔记从 Notion database 同步至 Readwise。


## Preparation

1. [将 flomo 同步到 Notion](https://help.flomoapp.com/advance/extension/notion-sync.html#%E8%A7%86%E9%A2%91%E6%95%99%E7%A8%8B)（需要 flomo 会员）
2. [配置 Notion](https://developers.notion.com/docs/create-a-notion-integration)
   - 创建一个 Notion Integration：https://www.notion.com/my-integrations
   - 在第1步中创建的 flomo database 中添加该 Integration
   - 获取该 Notion Integration 的 Token
   - 获取该 Notion Database 的 ID
3. 获取 Readwise Access Token: https://readwise.io/access_token


## Usage

1. Fork 这个项目到你自己的 GitHub 账户中
2. 删除 `last_sync_time.txt` 文件和 `flomo2readwise.log` 文件
   > 首次执行前请删除这两个文件。
   > 每次执行后，该项目会更新`last_sync_time.txt`文件，记录执行时间，以便在下次执行时只同步新的笔记。
3. 在你的仓库设置页面，进入 `Settings` → `Secrets and variables` → `Actions` 并添加以下 Repository secrets:
   - `NOTION_INTEGRATION_TOKEN`: 你的 Notion Integration Token
   - `NOTION_DATABASE_ID`: 你的 Notion Database ID
   - `READWISE_ACCESS_TOKEN`: 你的 Readwise Access Token

设置好以上步骤后，GitHub Actions 将会每天自动运行并将你的 flomo 笔记同步到 Readwise。


##  Others

1. 手动触发执行同步
   > 完成上述设置后，在你的仓库页面，进入 `Actions` → `Sync flomo from Notion database to Readwise`， 点击`Run Workflow`
2. 修改同步时间
   > 修改 `.github/workflows/sync_flomo_to_readwise.yml` 文件中以下字段自定义执行时间和频率：
   ```
   schedule:
   	- cron: '0 3 * * *'  # Runs daily at 03:00 UTC
   ```