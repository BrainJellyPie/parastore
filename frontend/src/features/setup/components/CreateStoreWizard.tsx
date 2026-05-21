import { useCallback, useState } from "react";

import { Button } from "@/shared/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/shared/components/ui/alert-dialog";
import { useCreateStore } from "@/shared/mutations/useCreateStore";

import {
  DEFAULT_VALUES,
  buildWeeklySchedule,
  validateStep1,
  validateStep2,
  type Step1Errors,
  type Step2Errors,
  type WizardValues,
} from "../validate";
import { Step1Fields } from "./Step1Fields";
import { Step2Fields } from "./Step2Fields";
import { WizardHeader } from "./WizardHeader";

interface CreateStoreWizardProps {
  onCreated?: (projectId: string) => void;
}

const STEPS = [
  { index: 1, label: "Configure new store" },
  { index: 2, label: "Generate synthetic consumers" },
] as const;

export function CreateStoreWizard({ onCreated }: CreateStoreWizardProps = {}) {
  const [step, setStep] = useState<1 | 2>(1);
  const [values, setValues] = useState<WizardValues>(DEFAULT_VALUES);
  const [step1Errors, setStep1Errors] = useState<Step1Errors | null>(null);
  const [step2Errors, setStep2Errors] = useState<Step2Errors | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const create = useCreateStore();

  const onChange = useCallback(
    <K extends keyof WizardValues>(key: K, value: WizardValues[K]) => {
      setValues((prev) => ({ ...prev, [key]: value }));
    },
    [],
  );

  const handleNext = useCallback(() => {
    const r = validateStep1(values);
    if (!r.ok) {
      setStep1Errors(r.errors);
      return;
    }
    setStep1Errors(null);
    setStep(2);
  }, [values]);

  const handleSubmitClick = useCallback(() => {
    const r1 = validateStep1(values);
    const r2 = validateStep2(values);
    if (!r1.ok) setStep1Errors(r1.errors);
    if (!r2.ok) setStep2Errors(r2.errors);
    if (!r1.ok || !r2.ok) return;
    setStep1Errors(null);
    setStep2Errors(null);
    setConfirmOpen(true);
  }, [values]);

  const handleConfirmedSubmit = useCallback(async () => {
    setConfirmOpen(false);
    try {
      const res = await create.mutateAsync({
        meta: {
          name: values.name.trim(),
          description: values.description,
          address: values.address.trim(),
          store_type: values.storeType.trim(),
          customer_profile: values.customerProfile.trim(),
          weekly_schedule: buildWeeklySchedule(values),
        },
        supplemental: values.supplementalFile,
      });
      onCreated?.(res.metadata.project_id);
    } catch {
      // create.error → rendered below
    }
  }, [values, create, onCreated]);

  const step1Ok = validateStep1(values).ok;
  const step2Ok = validateStep2(values).ok;
  const errMessage = create.error instanceof Error
    ? create.error.message
    : null;
  const isPending = create.isPending;

  return (
    <div className="flex-1 overflow-y-auto bg-background">
      <div className="mx-auto w-full max-w-2xl space-y-8 p-8">
        <WizardHeader title="Create new store" steps={STEPS} activeIndex={step} />

        {step === 1 && (
          <Step1Fields
            values={values}
            errors={step1Errors ?? undefined}
            disabled={isPending}
            onChange={onChange}
          />
        )}
        {step === 2 && (
          <Step2Fields
            values={values}
            errors={step2Errors ?? undefined}
            disabled={isPending}
            onChange={onChange}
          />
        )}

        {errMessage && step === 2 && (
          <p className="text-sm text-destructive">{errMessage}</p>
        )}

        <div className="flex items-center justify-between">
          {step === 2 ? (
            <Button type="button" variant="outline" disabled={isPending} onClick={() => setStep(1)}>
              Back
            </Button>
          ) : (
            <span />
          )}
          {step === 1 ? (
            <Button type="button" disabled={!step1Ok} onClick={handleNext}>
              Next
            </Button>
          ) : (
            <Button type="button" disabled={!step1Ok || !step2Ok || isPending} onClick={handleSubmitClick}>
              {isPending ? "Creating store…" : "Create new store"}
            </Button>
          )}
        </div>
      </div>
      <AlertDialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <AlertDialogContent className="data-[size=default]:sm:max-w-lg">
          <AlertDialogHeader>
            <AlertDialogTitle>Generate personas?</AlertDialogTitle>
            <AlertDialogDescription>
              This will consume API tokens based on your daily visitor cap. Continue?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmedSubmit}>Generate</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
