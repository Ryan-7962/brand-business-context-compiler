# src 说明

此目录用于 Python CLI 骨架。第一版实现范围：

- 初始化项目目录。
- 将 `source/` 下 PDF 转成带页码锚点、页面截图和质量报告的 Markdown 中间稿。
- 生成第一阶段 Marketing 语义底稿和 Brand Context Asset 模板文件。
- 支持生成 Document Profile、Marketing Semantic Transcript、Strategy and Execution Map 等默认输出骨架。
- 支持生成 Context Asset Index，作为后续派生 Skill 的调用索引。
- 支持生成 Context Library Update Plan，说明本次资料如何并入长期品牌上下文知识库。
- 支持将 Context Library Update Plan 写入本地 `brand_context_library/`。
- 产品资料可选模块中，保留 Brand Lock Sheet Draft 和 Claim Matrix 基础校验。
- 检查外发安全文本是否含内部敏感字段。
- 输出质量检查报告。

第一版不接复杂模型 API，不做 Web UI，不做企业级 RAG，也不自动生成完整 GEO/PDP/拍摄/种草 brief。
