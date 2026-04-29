import { useContext } from "react";
import { OrderContext } from "../context/OrderContext";

export const useOrder = () => useContext(OrderContext);