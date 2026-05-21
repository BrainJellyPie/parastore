import { cn } from "@/shared/utils/cn";
import { Input } from "@/shared/components/ui/input";
import { Textarea } from "@/shared/components/ui/textarea";

import type { Step1Errors } from "../validate";

const labelClass = "text-sm font-medium";
const errorTextClass = "text-xs text-destructive";
const errorBorderClass = "border-destructive focus-visible:border-destructive";

export interface StoreInfoFieldsProps {
  name: string;
  description: string;
  address: string;
  storeType: string;
  onNameChange: (value: string) => void;
  onDescriptionChange: (value: string) => void;
  onAddressChange: (value: string) => void;
  onStoreTypeChange: (value: string) => void;
  errors?: Pick<Step1Errors, "name" | "address" | "storeType">;
  disabled?: boolean;
}

export function StoreInfoFields({
  name,
  description,
  address,
  storeType,
  onNameChange,
  onDescriptionChange,
  onAddressChange,
  onStoreTypeChange,
  errors,
  disabled,
}: StoreInfoFieldsProps) {
  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <label className={labelClass} htmlFor="setup-store-name">
          Store name
        </label>
        <Input
          id="setup-store-name"
          className={cn(errors?.name && errorBorderClass)}
          value={name}
          placeholder="e.g., Downtown Convenience Store"
          disabled={disabled}
          aria-invalid={errors?.name ? true : undefined}
          onChange={(e) => onNameChange(e.target.value)}
        />
        {errors?.name && <p className={errorTextClass}>{errors.name}</p>}
      </div>

      <div className="space-y-1.5">
        <label className={labelClass} htmlFor="setup-store-description">
          Description (optional)
        </label>
        <Textarea
          id="setup-store-description"
          value={description}
          rows={3}
          disabled={disabled}
          onChange={(e) => onDescriptionChange(e.target.value)}
        />
      </div>

      <div className="space-y-1.5">
        <label className={labelClass} htmlFor="setup-store-address">
          Address
        </label>
        <Input
          id="setup-store-address"
          className={cn(errors?.address && errorBorderClass)}
          value={address}
          placeholder="e.g., 123 Main St, Seoul"
          disabled={disabled}
          aria-invalid={errors?.address ? true : undefined}
          onChange={(e) => onAddressChange(e.target.value)}
        />
        <p className="text-xs text-muted-foreground">
          Synthetic customers are automatically generated based on the demographics of your store's location.
        </p>
        {errors?.address && <p className={errorTextClass}>{errors.address}</p>}
      </div>

      <div className="space-y-1.5">
        <label className={labelClass} htmlFor="setup-store-type">
          Store type
        </label>
        <Input
          id="setup-store-type"
          className={cn(errors?.storeType && errorBorderClass)}
          value={storeType}
          placeholder="e.g., Convenience store"
          disabled={disabled}
          aria-invalid={errors?.storeType ? true : undefined}
          onChange={(e) => onStoreTypeChange(e.target.value)}
        />
        {errors?.storeType && <p className={errorTextClass}>{errors.storeType}</p>}
      </div>
    </div>
  );
}
