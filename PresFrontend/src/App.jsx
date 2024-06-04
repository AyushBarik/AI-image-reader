import { useState, useEffect } from "react";
import axiosClient from "./api/axiosClient";
import "./App.css";

function App() {
  const [hovered, setHovered] = useState(null);
  const [image, setImage] = useState(null);
  const [text, setText] = useState("");

  const handleMouseEnter = (box) => setHovered(box);
  const handleMouseLeave = () => setHovered(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => setImage(reader.result);
      reader.readAsDataURL(file);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axiosClient.get("/get-house-number");
        setText(res.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
  }, []);

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
              "Output"
            )}
          </div>
        ))}
      </div>
      <p>{text}</p>
    </div>
  );
}

export default App;
