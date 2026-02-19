import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const mockApi = async (page: Page) => {
  await page.route("**/api/v1/auth/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "tripy-token",
        token_type: "bearer",
        expires_in: 3600,
        roles: ["admin"],
        permissions: ["graph:execute", "users:read"]
      })
    });
  });

  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        username: "admin",
        real_name: null,
        email: "admin@example.com",
        phone: null,
        passenger_id: "P-100",
        is_active: true,
        roles: ["admin"],
        permissions: ["graph:execute", "users:read"]
      })
    });
  });

  await page.route("**/api/v1/graph/execute", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        assistant: "Mocked graph response",
        thread_id: "thread-1",
        interrupted: false
      })
    });
  });

  await page.route("**/api/v1/admin/users**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: 1,
          username: "admin",
          real_name: null,
          email: "admin@example.com",
          phone: null,
          passenger_id: "P-100",
          is_active: true,
          roles: ["admin"],
          permissions: ["graph:execute", "users:read"]
        }
      ])
    });
  });

  await page.route("**/api/v1/health/live", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok" })
    });
  });

  await page.route("**/api/v1/health/ready", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok" })
    });
  });

};

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test("login + conversation + admin flow works", async ({ page }) => {
  await page.goto("/");

  await page.getByTestId("login-button").click();
  await expect(page.getByTestId("login-button")).toBeDisabled();

  await page.getByTestId("assistant-input").fill("Please plan a route.");
  await page.getByTestId("assistant-send").click();
  await expect(page.getByText("Mocked graph response")).toBeVisible();

  await page.getByTestId("tab-admin").focus();
  await page.keyboard.press("Enter");
  await expect(page.getByTestId("admin-panel")).toBeVisible();

  await page.getByTestId("admin-refresh-users").click();
  const firstRow = page.locator("tbody tr").first();
  await expect(firstRow).toContainText("admin");
  await expect(firstRow).toContainText("users:read");
});

test("quick prompts and keyboard tab navigation work", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("login-button").click();

  await page.getByTestId("quick-prompt-assistant.prompt.route").click();
  const input = page.getByTestId("assistant-input");
  await expect(input).not.toHaveValue("");

  await page.getByTestId("tab-assistant").focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.getByTestId("tab-identity")).toHaveAttribute("aria-selected", "true");

  await page.keyboard.press("End");
  await expect(page.getByTestId("tab-system")).toHaveAttribute("aria-selected", "true");

  await page.keyboard.press("Home");
  await expect(page.getByTestId("tab-assistant")).toHaveAttribute("aria-selected", "true");
});

test("a11y audit has no serious violations", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page }).analyze();

  const serious = results.violations.filter(
    (violation) => violation.impact === "serious" || violation.impact === "critical"
  );

  expect(serious).toEqual([]);
});
