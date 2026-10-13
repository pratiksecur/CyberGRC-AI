import { toast } from "sonner";

/*
 * One place for messages shown to the person using the app.
 *
 * notify.success / notify.error show a toast instead of a browser alert().
 * confirmAction() replaces window.confirm(): it opens the confirmation
 * dialog (see ConfirmHost) and resolves to true or false.
 */

export const notify = {
  success(message: string) {
    toast.success(message);
  },

  error(message: string) {
    toast.error(message);
  },

  info(message: string) {
    toast(message);
  },
};

export interface ConfirmRequest {
  message: string;
  resolve: (confirmed: boolean) => void;
}

type ConfirmListener = (request: ConfirmRequest) => void;

let listener: ConfirmListener | null = null;

export function registerConfirmListener(next: ConfirmListener | null) {
  listener = next;
}

export function confirmAction(message: string): Promise<boolean> {
  return new Promise((resolve) => {
    if (!listener) {
      /* The dialog is not mounted (should not happen): never delete
         anything without an explicit yes. */
      resolve(false);
      return;
    }

    listener({ message, resolve });
  });
}
