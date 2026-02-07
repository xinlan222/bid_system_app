
import { registerOTel } from "@vercel/otel";

export function register() {
  registerOTel({
    serviceName: "bid_system_app-frontend",
  });
}
