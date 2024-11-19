interface RarityLabelProps {
  value: string | number;
  showCount?: boolean;
}

const RarityLabel: React.FC<RarityLabelProps> = ({ value, showCount = true }) => {
  const parseValue = (val: string | number): number => {
    if (typeof val === 'number') return val;
    return parseInt(val.replace(/[^0-9]/g, ''));
  };

  const getRarityInfo = (count: number): { label: string; color: string } => {
    if (count <= 10) {
      return { label: 'Mythic', color: 'from-purple-400 to-purple-600' };
    } else if (count <= 1000) {
      return { label: 'Ultra Rare', color: 'from-red-400 to-red-600' };
    } else if (count <= 5000) {
      return { label: 'Super Rare', color: 'from-orange-400 to-orange-600' };
    } else if (count <= 10000) {
      return { label: 'Rare', color: 'from-yellow-400 to-yellow-600' };
    } else if (count <= 100000) {
      return { label: 'Uncommon', color: 'from-green-400 to-green-600' };
    } else {
      return { label: 'Common', color: 'from-blue-400 to-blue-600' };
    }
  };

  const count = parseValue(value);
  const { label, color } = getRarityInfo(count);
  const formattedCount = count.toLocaleString();

  return (
    <div className="flex items-center gap-2">
      <span className="font-semibold text-gray-700 min-w-[120px]">Rarity:</span>
      <div className="flex items-center gap-2">
        <span className={`px-3 py-1 rounded-full text-white text-sm font-medium bg-gradient-to-r ${color}`}>
          {label}
        </span>
        {showCount && (
          <span className="text-gray-600">
            ({formattedCount} units)
          </span>
        )}
      </div>
    </div>
  );
};

export default RarityLabel; 