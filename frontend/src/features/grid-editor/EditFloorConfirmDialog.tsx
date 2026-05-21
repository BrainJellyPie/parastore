import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Button } from "@/shared/components/ui/button";

interface EditFloorConfirmDialogProps {
  open: boolean;
  onCancel: () => void;
  onConfirm: () => void;
  error?: string | null;
  confirmDisabled?: boolean;
}

export function EditFloorConfirmDialog({
  open,
  onCancel,
  onConfirm,
  error,
  confirmDisabled,
}: EditFloorConfirmDialogProps) {
  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (!next) onCancel();
      }}
    >
      <DialogContent data-testid="edit-floor-confirm-dialog">
        <DialogHeader>
          <DialogTitle>Edit floor configuration</DialogTitle>
          <DialogDescription>
            Please note that all existing item placement information will be reset.
          </DialogDescription>
        </DialogHeader>
        {error && (
          <p
            data-testid="edit-floor-confirm-error"
            className="rounded-md border border-destructive/40 bg-destructive/5 p-2 text-sm text-destructive"
          >
            {error}
          </p>
        )}
        <DialogFooter>
          <Button variant="outline" disabled={confirmDisabled} onClick={onCancel}>
            Cancel
          </Button>
          <Button variant="destructive" disabled={confirmDisabled} onClick={onConfirm}>
            Edit floor configuration
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
