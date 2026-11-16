import type {
  CrosswalkConfidence,
  CrosswalkTheme,
} from "@/api/frameworkCrosswalk";

/*
 * Small display pieces shared by the crosswalk views.
 */

export function ConfidenceBadge({
  confidence,
}: {
  confidence: CrosswalkConfidence;
}) {
  const direct = confidence === "direct";

  return (
    <span
      title={
        direct
          ? "Both requirements focus on the same theme."
          : "At least one of the requirements is broad, so the link is looser."
      }
      className={
        direct
          ? "rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-700"
          : "rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-700"
      }
    >
      {direct ? "Direct match" : "Broad match"}
    </span>
  );
}

export function ThemeChips({
  themes,
}: {
  themes: CrosswalkTheme[];
}) {
  if (themes.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-1.5">
      {themes.map((theme) => (
        <span
          key={theme.key}
          className="rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-600"
        >
          {theme.label}
        </span>
      ))}
    </div>
  );
}

export function CrosswalkDisclaimer() {
  return (
    <p className="text-xs text-slate-500">
      Suggestions come from a thematic crosswalk written for this platform.
      It is not an official mapping, and a shared theme does not mean two
      requirements are equivalent. Review each one before applying it.
    </p>
  );
}
