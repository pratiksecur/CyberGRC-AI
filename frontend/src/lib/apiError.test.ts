import { AxiosError, AxiosHeaders } from "axios";
import { describe, expect, it } from "vitest";

import { apiErrorMessage } from "./apiError";

const FALLBACK = "Failed to save.";

function failure(status: number, data: unknown) {
  return new AxiosError(
    "Request failed",
    "ERR_BAD_REQUEST",
    undefined,
    undefined,
    {
      status,
      statusText: "",
      data,
      headers: {},
      config: { headers: new AxiosHeaders() },
    }
  );
}

describe("apiErrorMessage", () => {
  it("uses the fallback for errors that did not come from the API", () => {
    expect(apiErrorMessage(new Error("boom"), FALLBACK)).toBe(FALLBACK);
    expect(apiErrorMessage("oops", FALLBACK)).toBe(FALLBACK);
    expect(apiErrorMessage(undefined, FALLBACK)).toBe(FALLBACK);
  });

  it("explains when the server cannot be reached", () => {
    const error = new AxiosError("Network Error", "ERR_NETWORK");

    expect(apiErrorMessage(error, FALLBACK)).toMatch(/cannot reach the server/i);
  });

  it("shows the message from the application's own error handlers", () => {
    const error = failure(409, { error: { message: "Email already exists." } });

    expect(apiErrorMessage(error, FALLBACK)).toBe("Email already exists.");
  });

  it("shows a plain detail string", () => {
    const error = failure(400, { detail: "Password is too common." });

    expect(apiErrorMessage(error, FALLBACK)).toBe("Password is too common.");
  });

  it("joins FastAPI validation messages", () => {
    const error = failure(422, {
      detail: [{ msg: "Title is required." }, { msg: "Score is too high." }],
    });

    expect(apiErrorMessage(error, FALLBACK)).toBe(
      "Title is required. Score is too high."
    );
  });

  it("prefers the handler message over detail", () => {
    const error = failure(400, {
      error: { message: "From handler." },
      detail: "From detail.",
    });

    expect(apiErrorMessage(error, FALLBACK)).toBe("From handler.");
  });

  it("explains rate limiting and missing permission", () => {
    expect(apiErrorMessage(failure(429, {}), FALLBACK)).toMatch(/too many attempts/i);
    expect(apiErrorMessage(failure(403, {}), FALLBACK)).toMatch(/permission/i);
  });

  it("falls back when the response has nothing useful", () => {
    expect(apiErrorMessage(failure(500, {}), FALLBACK)).toBe(FALLBACK);
    expect(apiErrorMessage(failure(400, { detail: "   " }), FALLBACK)).toBe(FALLBACK);
    expect(apiErrorMessage(failure(422, { detail: [{}] }), FALLBACK)).toBe(FALLBACK);
  });
});
