import { Moon, Sun } from "@phosphor-icons/react";

interface DarkModeToggleProps {
  isDark: boolean;
  toggle: () => void;
}

const DarkModeToggle: React.FC<DarkModeToggleProps> = ({ isDark, toggle }) => {
  return (
    <button
      onClick={toggle}
      className="p-2 rounded-lg bg-gray-100 dark:bg-neutral-800 text-gray-800 dark:text-neutral-200 hover:bg-gray-200 dark:hover:bg-neutral-700 transition"
      aria-label="Toggle dark mode"
    >
      {isDark ? (
        <Sun size={24} weight="bold" />
      ) : (
        <Moon size={24} weight="bold" />
      )}
    </button>
  );
};

export default DarkModeToggle;
