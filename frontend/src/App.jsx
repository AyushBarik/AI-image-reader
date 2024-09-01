import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [hovered, setHovered] = useState(null);
  const [image, setImage] = useState(null);
  const [text, setText] = useState("");
  const [response, setResponse] = useState("");

  const handleMouseEnter = (box) => setHovered(box);
  const handleMouseLeave = () => setHovered(null);

  const handleSubmit = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setResponse(res.data.message);
    } catch (error) {
      console.error("Error uploading image:", error);
      setResponse("Error uploading image");
    }
  };

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setImage(reader.result);
      };
      reader.readAsDataURL(file);
      handleSubmit(file); // Call handleSubmit with the selected file
    }
  };

  const handleOutputClick = async () => {
    try {
      const response = await axios.get("http://localhost:8000/fetchResponse", {
        responseType: "blob",
      });

      const audioUrl = URL.createObjectURL(response.data);

      const audioElement = new Audio(audioUrl);

      audioElement.play();
    } catch (error) {
      console.error("Error fetching audio:", error);
    }
  };

  return (
    <div>
      <div className="image-container">
        {image && <img src={image} alt="Uploaded" className="uploaded-image" />}
      </div>
      <div className="container">
        {["box1", "box2"].map((box) => (
          <div
            key={box}
            className={`box ${
              hovered === box ? `${box}-hover` : hovered && `${hovered}-small`
            }`}
            onMouseEnter={() => handleMouseEnter(box)}
            onMouseLeave={handleMouseLeave}
          >
            {box === "box1" ? (
              <>
                <label htmlFor="imageUpload" className="upload-label">
                  Input
                </label>
                <input
                  id="imageUpload"
                  type="file"
                  accept="image/*"
                  style={{ display: "none" }}
                  onChange={handleImageUpload}
                />
              </>
            ) : (
              <button className="button" onClick={handleOutputClick}>
                AI Response
              </button>
            )}
          </div>
        ))}
      </div>
      <p>{text}</p>
    </div>
  );
}

export default App;
