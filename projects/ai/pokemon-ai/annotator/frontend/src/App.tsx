import { BrowserRouter, Routes, Route } from "react-router-dom";
import Gallery from "./Gallery";
import Detail from "./Detail";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Gallery />} />
        <Route path="/annotation/:id" element={<Detail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
