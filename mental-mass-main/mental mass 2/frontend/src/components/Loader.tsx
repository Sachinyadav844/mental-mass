import { Brain } from "lucide-react";

const Loader = ({ message = "Loading..." }: { message?: string }) => (
  <div className="flex flex-col items-center justify-center gap-4 py-16">
    <div className="relative">
      <div className="w-14 h-14 rounded-full border-4 border-primary/20 border-t-primary animate-spin" />
      <Brain className="absolute inset-0 m-auto w-6 h-6 text-primary" />
    </div>
    <p className="text-muted-foreground text-sm font-medium animate-pulse">
      {message}
    </p>
  </div>
);

export default Loader;
