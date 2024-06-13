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
    // const file = event.target.files[0];
    // if (file) {
    //   setImage(URL.createObjectURL(file));
    //   handleSubmit(file);
    // }
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

      // Create a URL for the audio blob
      const audioUrl = URL.createObjectURL(response.data);

      // Create an <audio> element
      const audioElement = new Audio(audioUrl);

      // Play the audio
      audioElement.play();
    } catch (error) {
      console.error("Error fetching audio:", error);
    }
    // try {
    //   const response = await axios.get(
    //     "http://localhost:8000/download_response",
    //     {
    //       responseType: "blob",
    //     }
    //   );

    //   // Create a URL for the file
    //   const url = window.URL.createObjectURL(new Blob([response.data]));

    //   const link = document.createElement("a");
    //   link.href = url;
    //   link.setAttribute("download", "response.txt");

    //   document.body.appendChild(link);
    //   link.click();
    //   document.body.removeChild(link);

    //   window.URL.revokeObjectURL(url);
    // } catch (error) {
    //   console.error("Error downloading file", error);
    // }
  };

  // useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       const res = await axios.get("http://localhost:8000/fetchResponse");
  //       setText(res.data);
  //     } catch (error) {
  //       console.error("Error fetching data:", error);
  //     }
  //   };
  //   fetchData();
  // }, []);

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
