import { useEffect, useState } from "react";
import HeaderBar from "../components/KDS/HeaderBar";
import StationRow from "../components/KDS/StationRow";
import "./KDS.css";

export default function KDSPage() {
  const [stations, setStations] = useState([]);
  const [ticketsMap, setTicketsMap] = useState({});
  const [menuItems, setMenuItems] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      // Fetch menu items (one-time or less frequent)
      if (Object.keys(menuItems).length === 0) {
        try {
          const menuRes = await fetch("/api/v1/menu/items");
          if (menuRes.ok) {
            const menuData = await menuRes.json();
            if (Array.isArray(menuData)) {
              const menuMap = {};
              menuData.forEach((item) => {
                menuMap[item.id] = item;
              });
              setMenuItems(menuMap);
            }
          }
        } catch (err) {
          console.warn("Failed to fetch menu items:", err);
          // Continue without menu items - we'll show generic names
        }
      }

      // Fetch stations and tickets
      const res = await fetch("/api/v1/kds/stations");
      const stationsData = await res.json();
      setStations(stationsData);

      const results = await Promise.all(
        stationsData.map(async (station) => {
          const t = await fetch(
            `/api/v1/kds/stations/${station.id}/tickets?status=ACTIVE`
          );
          return {
            stationId: station.id,
            tickets: await t.json(),
          };
        })
      );

      const map = {};
      results.forEach(({ stationId, tickets }) => {
        map[stationId] = tickets;
      });

      setTicketsMap(map);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch KDS data:", err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loading">Loading KDS...</div>;

  return (
    <div className="kds-container">
      <HeaderBar />

      <div className="kds-content">
        {stations.map((station) => (
          <StationRow
            key={station.id}
            station={station}
            tickets={ticketsMap[station.id] || []}
            menuItems={menuItems}
          />
        ))}
      </div>
    </div>
  );
}