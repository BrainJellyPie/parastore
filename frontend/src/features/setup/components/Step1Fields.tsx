import { OpeningHoursField } from "./OpeningHoursField";
import { StoreInfoFields } from "./StoreInfoFields";
import { WeeklyScheduleField } from "./WeeklyScheduleField";
import type { Step1Errors, WizardValues } from "../validate";

interface Step1FieldsProps {
  values: WizardValues;
  errors: Step1Errors | undefined;
  disabled?: boolean;
  onChange: <K extends keyof WizardValues>(key: K, value: WizardValues[K]) => void;
}

export function Step1Fields({ values, errors, disabled, onChange }: Step1FieldsProps) {
  // StoreInfoFields.errors is typed as Pick<Step1Errors, "name" | "address" | "storeType">.
  // Narrow the full Step1Errors to the subset the sub-component accepts.
  const infoErrors: Pick<Step1Errors, "name" | "address" | "storeType"> | undefined =
    errors
      ? { name: errors.name, address: errors.address, storeType: errors.storeType }
      : undefined;

  return (
    <div className="space-y-6">
      <StoreInfoFields
        name={values.name}
        description={values.description}
        address={values.address}
        storeType={values.storeType}
        onNameChange={(v) => onChange("name", v)}
        onDescriptionChange={(v) => onChange("description", v)}
        onAddressChange={(v) => onChange("address", v)}
        onStoreTypeChange={(v) => onChange("storeType", v)}
        errors={infoErrors}
        disabled={disabled}
      />
      <WeeklyScheduleField
        value={values.workingDayPreset}
        onChange={(v) => onChange("workingDayPreset", v)}
        disabled={disabled}
      />
      <OpeningHoursField
        openHour={values.openHour}
        closeHour={values.closeHour}
        onOpenChange={(v) => onChange("openHour", v)}
        onCloseChange={(v) => onChange("closeHour", v)}
        openError={errors?.openHour}
        closeError={errors?.closeHour}
        disabled={disabled}
      />
    </div>
  );
}
