import { useNavigate } from "react-router-dom";
import "./WelcomePage.css";

function WelcomePage() {
  const navigate = useNavigate();

  return (
    <div className="welcome-page">
      <div className="overlay">
        <h1>WELCOME TO IRMS</h1>

        <button
          className="enter-btn"
          onClick={() => navigate("/create-order")}
        >
          Create Order
        </button>
      </div>
    </div>
  );
}

export default WelcomePage;