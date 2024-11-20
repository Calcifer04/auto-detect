import {
  CurrencyDollar,
  Engine,
  Horse,
  Timer,
  Gear,
  Speedometer,
  GasPump,
  Scales,
  Info,
  NumberCircleOne,
  CalendarBlank
} from "@phosphor-icons/react";

interface CarDetailsProps {
  model_year: string;
  estimated_value: string;
  horsepower: string;
  top_speed: string;
  acceleration: string;
  engine: string;
  transmission: string;
  fuel_consumption: string;
  weight: string;
  units_made: string;
  fun_fact: string;
}

const DetailRow = ({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) => (
  <div className="flex items-center gap-3 p-2 border-b border-gray-100 dark:border-neutral-800">
    <div className="text-xl">{icon}</div>
    <div className="flex-1">
      <div className="text-sm text-gray-500 dark:text-neutral-400">{label}</div>
      <div className="font-medium text-gray-900 dark:text-neutral-100">{value}</div>
    </div>
  </div>
);

const CarDetails: React.FC<CarDetailsProps> = ({
  model_year,
  estimated_value,
  horsepower,
  top_speed,
  acceleration,
  engine,
  transmission,
  fuel_consumption,
  weight,
  units_made,
  fun_fact
}) => {
  return (
    <div className="space-y-1 bg-white dark:bg-neutral-900 rounded-lg shadow-[0_4px_12px_rgba(0,0,0,0.1)] dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)] p-4">
      
      <DetailRow 
        icon={<CalendarBlank size={24} weight="bold" className="text-amber-500 dark:text-amber-400" />} 
        label="Model Year" 
        value={model_year} 
      />
      <DetailRow 
        icon={<CurrencyDollar size={24} weight="bold" className="text-green-500 dark:text-green-400" />} 
        label="Estimated Value" 
        value={estimated_value} 
      />
      <DetailRow 
        icon={<Horse size={24} weight="bold" className="text-red-500 dark:text-red-400" />} 
        label="Horsepower" 
        value={horsepower} 
      />
      <DetailRow 
        icon={<Speedometer size={24} weight="bold" className="text-blue-500 dark:text-blue-400" />} 
        label="Top Speed" 
        value={top_speed} 
      />
      <DetailRow 
        icon={<Timer size={24} weight="bold" className="text-purple-500 dark:text-purple-400" />} 
        label="0-100 km/h" 
        value={acceleration} 
      />
      <DetailRow 
        icon={<Engine size={24} weight="bold" className="text-orange-500 dark:text-orange-400" />} 
        label="Engine" 
        value={engine} 
      />
      <DetailRow 
        icon={<Gear size={24} weight="bold" className="text-indigo-500 dark:text-indigo-400" />} 
        label="Transmission" 
        value={transmission} 
      />
      <DetailRow 
        icon={<GasPump size={24} weight="bold" className="text-cyan-500 dark:text-cyan-400" />} 
        label="Fuel Consumption" 
        value={fuel_consumption} 
      />
      <DetailRow 
        icon={<Scales size={24} weight="bold" className="text-teal-500 dark:text-teal-400" />} 
        label="Weight" 
        value={weight} 
      />
      <DetailRow 
        icon={<NumberCircleOne size={24} weight="bold" className="text-pink-500 dark:text-pink-400" />} 
        label="Units Made" 
        value={units_made} 
      />
      
      <div className="mt-4 p-3 bg-gray-50 dark:bg-neutral-800 rounded-lg">
        <div className="flex items-start gap-2">
          <Info size={24} weight="bold" className="text-blue-500 dark:text-blue-400" />
          <div>
            <div className="font-medium text-gray-900 dark:text-neutral-100">Fun Fact</div>
            <div className="text-gray-600 dark:text-neutral-400">{fun_fact}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CarDetails; 