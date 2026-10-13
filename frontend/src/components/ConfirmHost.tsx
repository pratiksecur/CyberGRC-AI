import { useEffect, useRef, useState } from "react";

import {
  registerConfirmListener,
  type ConfirmRequest,
} from "@/lib/notify";

/*
 * Renders the confirmation dialog used by confirmAction().
 * Mount it once, near the root of the app.
 */
export default function ConfirmHost() {
  const [request, setRequest] = useState<ConfirmRequest | null>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    registerConfirmListener((next) => setRequest(next));

    return () => registerConfirmListener(null);
  }, []);

  useEffect(() => {
    if (request) {
      cancelRef.current?.focus();
    }
  }, [request]);

  function answer(confirmed: boolean) {
    request?.resolve(confirmed);
    setRequest(null);
  }

  useEffect(() => {
    if (!request) return;

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        request?.resolve(false);
        setRequest(null);
      }
    }

    window.addEventListener("keydown", onKeyDown);

    return () => window.removeEventListener("keydown", onKeyDown);
  }, [request]);

  if (!request) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4"
      onClick={() => answer(false)}
    >
      <div
        role="alertdialog"
        aria-modal="true"
        aria-label="Please confirm"
        className="w-full max-w-md rounded-xl border bg-white p-6 shadow-xl dark:border-slate-700 dark:bg-slate-900"
        onClick={(event) => event.stopPropagation()}
      >
        <p className="text-sm text-slate-800 dark:text-slate-100">
          {request.message}
        </p>

        <div className="mt-6 flex justify-end gap-3">
          <button
            ref={cancelRef}
            type="button"
            className="rounded-lg border px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-200 dark:hover:bg-slate-800"
            onClick={() => answer(false)}
          >
            Cancel
          </button>

          <button
            type="button"
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
            onClick={() => answer(true)}
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}
