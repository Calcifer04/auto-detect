interface StatSliderProps {
  label: string;
  value: string | number;
  max: number;
  unit: string;
  gradient: string;
  formatValue?: (value: number) => string;
  type?: 'price' | 'horsepower' | 'speed' | 'default';
}

const StatSlider: React.FC<StatSliderProps> = ({ 
  label, 
  value, 
  max, 
  unit, 
  gradient,
  formatValue,
  type = 'default'
}) => {
  const parsePrice = (str: string): number => {
    // Remove dollar signs and commas
    str = str.toLowerCase().replace(/[$,]/g, '');
    
    // Try to find a number followed by optional 'million'
    const millionMatch = str.match(/([\d.]+)\s*million/);
    if (millionMatch) {
      return parseFloat(millionMatch[1]) * 1000000;
    }
    
    // Try to find a number followed by 'm' for million
    const mMatch = str.match(/([\d.]+)m/);
    if (mMatch) {
      return parseFloat(mMatch[1]) * 1000000;
    }
    
    // Try to find any number
    const numberMatch = str.match(/([\d.]+)/);
    if (numberMatch) {
      return parseFloat(numberMatch[1]);
    }
    
    return 0;
  };

  const parseValue = (val: string | number): number => {
    if (typeof val === 'number') return val;
    const str = val.toLowerCase();

    switch (type) {
      case 'price':
        if (str.includes('-')) {
          // For ranges, take the first number
          const [firstPart] = str.split('-');
          return parsePrice(firstPart);
        }
        return parsePrice(str);

      case 'horsepower':
        const hpMatch = str.match(/(\d+)(?:\s*-\s*(\d+))?\s*hp/i);
        if (hpMatch) {
          return parseInt(hpMatch[2] || hpMatch[1]);
        }
        const firstHpNumber = str.match(/\d+/);
        return firstHpNumber ? parseInt(firstHpNumber[0]) : 0;

      case 'speed':
        const speedMatch = str.match(/(\d+)(?:\s*-\s*(\d+))?\s*(?:mph|km\/h)/i);
        if (speedMatch) {
          return parseInt(speedMatch[2] || speedMatch[1]);
        }
        const firstSpeedNumber = str.match(/\d+/);
        return firstSpeedNumber ? parseInt(firstSpeedNumber[0]) : 0;

      default:
        const matches = str.match(/\d+/);
        return matches ? parseInt(matches[0]) : 0;
    }
  };

  const numericValue = parseValue(value);
  console.log(`Parsing ${value} to ${numericValue}`); // Debug log
  const percentage = Math.min((numericValue / max) * 100, 100);

  const getDisplayValue = () => {
    if (type === 'price') {
      // For price, always show the original text
      return typeof value === 'string' ? value : formatValue?.(numericValue) || `$${numericValue.toLocaleString()}`;
    }
    
    if (formatValue) {
      return formatValue(numericValue);
    }
    
    // Show original string if it contains units or ranges
    if (typeof value === 'string' && 
       (value.includes('hp') || value.includes('km/h') || value.includes('mph'))) {
      return value.split('(')[0].trim();
    }
    
    return numericValue.toLocaleString() + (unit ? ` ${unit}` : '');
  };

  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-center">
        <span className="font-semibold text-gray-700">{label}</span>
        <span className="text-gray-600">{getDisplayValue()}</span>
      </div>
      <div className="h-3 w-full bg-gray-100 rounded-full overflow-hidden">
        <div 
          className={`h-full ${gradient} rounded-full transition-all duration-1000 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default StatSlider; 