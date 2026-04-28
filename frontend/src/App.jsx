import { BrowserRouter, Routes, Route } from "react-router-dom";
import OrderingPage from "./pages/OrderingPage";
import KDSPage from "./pages/KDSPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/order" element={<OrderingPage />} />
        <Route path="/kds" element={<KDSPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;