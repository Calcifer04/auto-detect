import React, { useState } from "react";
import axios from "axios";
import carIcon from "./assets/butterfly-shape 1(1).svg";
import loadWheel from "./assets/Wheel-4 1.svg"
import './index.css';

const App: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [prediction, setPrediction] = useState({
    make_model: "",
    price_range: "",
    horsepower: "",
    fun_fact: ""
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false); // Loading state

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedImage(event.target.files[0]);
    }
  };

  const analyzeImage = async () => {
    if (!selectedImage) return;

    const formData = new FormData();
    formData.append("image", selectedImage);

    setLoading(true); // Set loading to true when starting the request
    try {
      const response = await axios.post("http://127.0.0.1:5000/identify-car", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.data.error) {
        setError(response.data.error);
        setPrediction({
          make_model: "",
          price_range: "",
          horsepower: "",
          fun_fact: ""
        });
      } else {
        setError(null);
        setPrediction(response.data);
      }
    } catch (error) {
      console.error("Error analyzing image:", error);
      setError("An error occurred while analyzing the image.");
    } finally {
      setLoading(false); // Set loading to false after the request completes
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-dotted p-6">
      <img src={carIcon} alt="Car Icon" className="w-full h-36 relative top-4" />
      <header className="header text-7xl rounded-lg font-bold text-black-600 mb-2">
        AutoDetect
      </header>
  
      <div className=" p-8 rounded-lg w-full max-w-xl text-center">
        {selectedImage && (
          <div className="mb-1">
            <img
              src={URL.createObjectURL(selectedImage)}
              alt="Selected"
              className="w-full h-full object-cover rounded-md mb-4"
            />
          </div>
        )}
  
        <label
          htmlFor="image-upload"
          className="shadow-lg mt-0 cursor-pointer inline-block bg-rose-400 text-white font-semibold px-4 py-2 rounded-lg hover:bg-rose-600 transition mr-2"
        >
          Choose Image
        </label>
        <input
          id="image-upload"
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="hidden"
        />
  
        <button
          onClick={analyzeImage}
          className="shadow-lg mt-0 bg-violet-500 text-white font-semibold px-4 py-2 rounded-lg hover:bg-violet-800 transition ml-2"
        >
          Analyze Image
        </button>

        {/* Loading indicator */}
        {loading && (
          <div className="overlay">
          <div className="wheel-wrapper">
              <img src={loadWheel} className="rotating"/>
          </div>
      </div>
      
        )} 
        {error ? (
          <div className="mt-4 bg-red-100 p-4 rounded-lg text-red-800">
            <p>{error}</p>
          </div>
        ) : (
          !loading && prediction.make_model && (
            <div className="mt-4 bg-gray-200 p-4 rounded-lg text-left">
              <p><strong>Make and Model:</strong> {prediction.make_model}</p>
              <p><strong>Estimated Price:</strong> {prediction.price_range}</p>
              <p><strong>Horsepower:</strong> {prediction.horsepower}</p>
              <p><strong>Fun Fact:</strong> {prediction.fun_fact}</p>
            </div>
          )
        )}
      </div>
    </div>
  );  
};

export default App;
