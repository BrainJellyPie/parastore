// Pure-TS validators for the CreateStoreWizard. No React imports — keeps unit tests trivial.

export type WorkingDayPreset = "7" | "weekday" | "weekend";

export const DAY_PRESETS: readonly {
  value: WorkingDayPreset;
  label: string;
  days: readonly boolean[];
}[] = [
  { value: "7",       label: "7 Days",            days: [true, true, true, true, true, true, true] },
  { value: "weekday", label: "Weekday (Mon-Fri)", days: [true, true, true, true, true, false, false] },
  { value: "weekend", label: "Weekend (Sat-Sun)", days: [false, false, false, false, false, true, true] },
];

export interface WizardValues {
  // Step 1
  name: string;
  description: string;
  address: string;
  storeType: string;
  workingDayPreset: WorkingDayPreset;
  openHour: number;
  closeHour: number;
  // Step 2
  customerProfile: string;
  supplementalFile: File | null;
}

export interface Step1Errors {
  name?: string;
  address?: string;
  storeType?: string;
  openHour?: string;
  closeHour?: string;
}

export interface Step2Errors {
  customerProfile?: string;
  supplementalFile?: string;
}

export type WizardErrors = Step1Errors & Step2Errors;

export const DEFAULT_VALUES: WizardValues = {
  name: "",
  description: "",
  address: "",
  storeType: "",
  workingDayPreset: "7",
  openHour: 0,
  closeHour: 24,
  customerProfile: "",
  supplementalFile: null,
};

const SUPPLEMENTAL_ALLOWED_EXTS: ReadonlySet<string> = new Set(["csv", "xlsx"]);
const SUPPLEMENTAL_MAX_BYTES = 10 * 1024 * 1024;
const HOURS_RANGE_MSG = "Opening hours must satisfy 0 ≤ open < close ≤ 24";

export type Step1Result = { ok: true } | { ok: false; errors: Step1Errors };
export type Step2Result = { ok: true } | { ok: false; errors: Step2Errors };

function isValidHour(v: number): boolean {
  return Number.isInteger(v) && v >= 0 && v <= 24;
}

export function validateStep1(values: WizardValues): Step1Result {
  const errors: Step1Errors = {};

  if (values.name.trim().length < 1) errors.name = "Store name is required";
  if (values.address.trim().length < 1) errors.address = "Address is required";
  if (values.storeType.trim().length < 1) errors.storeType = "Store type is required";

  const openOk = isValidHour(values.openHour);
  const closeOk = isValidHour(values.closeHour);
  if (!openOk || !closeOk || values.openHour >= values.closeHour) {
    if (!openOk) errors.openHour = HOURS_RANGE_MSG;
    if (!closeOk || values.openHour >= values.closeHour) errors.closeHour = HOURS_RANGE_MSG;
  }

  return Object.keys(errors).length === 0 ? { ok: true } : { ok: false, errors };
}

export function validateStep2(values: WizardValues): Step2Result {
  const errors: Step2Errors = {};

  if (values.customerProfile.trim().length < 1) {
    errors.customerProfile = "Tell us about your customers";
  }

  if (values.supplementalFile) {
    const f = values.supplementalFile;
    const ext = f.name.includes(".") ? f.name.split(".").pop()!.toLowerCase() : "";
    if (!SUPPLEMENTAL_ALLOWED_EXTS.has(ext)) {
      errors.supplementalFile = "Unsupported format. Use .csv or .xlsx";
    } else if (f.size > SUPPLEMENTAL_MAX_BYTES) {
      errors.supplementalFile = "File is too large (max 10MB)";
    }
  }

  return Object.keys(errors).length === 0 ? { ok: true } : { ok: false, errors };
}

export interface DaySchedulePayload {
  day: number;
  is_open: boolean;
  open_hour: number;
  close_hour: number;
}

export function buildWeeklySchedule(values: WizardValues): DaySchedulePayload[] {
  const preset = DAY_PRESETS.find((p) => p.value === values.workingDayPreset)!;
  return preset.days.map((isOpen, i) => ({
    day: i + 1,
    is_open: isOpen,
    open_hour: values.openHour,
    close_hour: values.closeHour,
  }));
}
