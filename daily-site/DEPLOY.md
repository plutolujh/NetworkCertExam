# Cloudflare Pages 部署指南

## 方法一：直接上传（最简单）

### 1. 登录 Cloudflare Dashboard
访问 https://dash.cloudflare.com

### 2. 创建 Workers & Pages
- 点击 "Workers & Pages"
- 点击 "Create application"
- 选择 "Pages" → "Upload direct"

### 3. 上传文件
将 `daily-site/` 目录下的所有文件上传：
```
index.html
manifest.json
```

### 4. 设置自定义域名（可选）
- 输入你的域名
- 配置 DNS 指向 Cloudflare

---

## 方法二：Git 部署（推荐，持续更新）

### 1. 将 daily-site 推送到 GitHub
```bash
cd daily-site
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/plutolujh/networkcert-daily.git
git push -u origin main
```

### 2. 连接 Cloudflare Pages
- 在 Cloudflare Dashboard 创建新项目
- 选择 "Connect to Git"
- 选择你的 GitHub 仓库
- 构建命令留空
- 输出目录：`/`

### 3. 自动部署
以后每次推送到 GitHub，Cloudflare 会自动构建部署。

---

## 方法三：使用 Wrangler CLI

```bash
npm install -g wrangler
wrangler pages deploy daily-site
```

---

## 功能说明

当前 `index.html` 是静态页面，显示：
- 今日学习任务（可勾选）
- 综合知识考点
- 案例分析答题框架
- 论文写作素材
- 掌握进度

如需动态每日内容，可以：
1. **Cloudflare Workers**：创建 API 读取每日数据
2. **KV 存储**：存储每日学习进度

---

## 效果预览

部署后访问你的域名，即可看到：
- 手机端自适应页面
- 每日学习内容
- 考前倒计时
- 前后日期导航