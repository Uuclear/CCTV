import { expect, test } from "@playwright/test";

test("首页加载并新建项目", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "CCTV 检测报告工作台" })).toBeVisible();
  await page.getByTestId("project-name-input").fill("E2E 测试工程");
  await page.getByTestId("create-project-submit").click();
  await expect(page.getByText("E2E 测试工程").first()).toBeVisible({ timeout: 15_000 });
});
