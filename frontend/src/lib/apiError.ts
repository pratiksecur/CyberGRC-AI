import { AxiosError } from "axios";

/*
 * Turn any error from an API call into a sentence that can be shown to the
 * person using the app.
 *
 * The server's own explanation (for example "Password is too common.") is
 * used when there is one, so people see what actually went wrong instead of
 * a generic "Failed to ...".
 */
export function apiErrorMessage(
  error: unknown,
  fallback: string
): string {
  if (!(error instanceof AxiosError)) {
    return fallback;
  }

  if (!error.response) {
    return "Cannot reach the server. Check your connection and try again.";
  }

  /* Errors raised by the application's own handlers look like
     { error: { message } } instead of { detail }. */
  const handlerMessage = error.response.data?.error?.message;

  if (typeof handlerMessage === "string" && handlerMessage.trim()) {
    return handlerMessage;
  }

  const detail = error.response.data?.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  /* FastAPI validation errors arrive as a list of { msg } objects. */
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) =>
        typeof item?.msg === "string" ? item.msg : ""
      )
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join(" ");
    }
  }

  if (error.response.status === 429) {
    return "Too many attempts. Please wait a few minutes and try again.";
  }

  if (error.response.status === 403) {
    return "You do not have permission to do that.";
  }

  return fallback;
}
