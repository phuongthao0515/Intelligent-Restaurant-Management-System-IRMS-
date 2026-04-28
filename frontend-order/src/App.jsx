import { Routes, Route } from "react-router-dom";
import WelcomePage from "./pages/WelcomePage";
import OrderingPage from "./pages/OrderingPage";
import OrderListPage from "./pages/OrderListPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<WelcomePage />} />
      <Route path="/create-order" element={<OrderingPage />} />
      <Route path="/orders" element={<OrderListPage />} />
    </Routes>
  );
}

export default App;