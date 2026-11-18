import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Directorio de proveedores | HealthCore",
  description: "Backoffice para gestionar proveedores de HealthCore.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}
