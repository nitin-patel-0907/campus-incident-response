import { ReactNode } from "react";
import { AppSidebar } from "./AppSidebar";

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <AppSidebar />
      <main className="ml-16 lg:ml-64 min-h-screen transition-all duration-300">
        <div className="container mx-auto px-4 py-6 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  );
}
