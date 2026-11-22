// Optional scheduled rebuild so new ratings are picked up even when nobody deploys.
// BUILD_HOOK_URL is a secret: set it in the Netlify UI, never in the repo.
export default async () => {
  const hook = process.env.BUILD_HOOK_URL;
  if (!hook) {
    console.log("BUILD_HOOK_URL is not set; skipping rebuild.");
    return;
  }
  const res = await fetch(hook, { method: "POST", body: "{}" });
  console.log(`Rebuild requested, status ${res.status}`);
};

export const config = { schedule: "@daily" };
