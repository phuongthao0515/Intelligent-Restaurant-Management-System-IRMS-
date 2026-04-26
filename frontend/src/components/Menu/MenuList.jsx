import MenuItem from "./MenuItem";

const mockMenu = [
  { id: 1, name: "Burger", price: 5 },
  { id: 2, name: "Pizza", price: 8 },
  { id: 3, name: "Pasta", price: 7 },
];

function MenuList() {
  return (
    <div>
      {mockMenu.map((item) => (
        <MenuItem key={item.id} item={item} />
      ))}
    </div>
  );
}

export default MenuList;