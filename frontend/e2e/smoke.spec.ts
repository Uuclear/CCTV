import { expect, test } from "@playwright/test";

test("首页加载并新建项目", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "CCTV 检测报告工作台" })).toBeVisible();
  await page.getByTestId("project-name-input").fill("E2E 测试工程");
  await page.getByTestId("create-project-submit").click();
  await expect(page.getByText("E2E 测试工程").first()).toBeVisible({ timeout: 15_000 });
});

test("工作台：新建管段", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("project-name-input").fill("E2E 工作台工程");
  await page.getByTestId("create-project-submit").click();
  await expect(page.getByText("E2E 工作台工程").first()).toBeVisible({ timeout: 15_000 });
  await page.getByRole("button", { name: "进入工作台" }).first().click();
  await expect(page.getByRole("heading", { name: "E2E 工作台工程" })).toBeVisible({ timeout: 10_000 });
  await page.getByTestId("add-segment").click();
  await expect(page.locator("[data-testid^=\"segment-\"]").first()).toBeVisible({ timeout: 10_000 });
});
