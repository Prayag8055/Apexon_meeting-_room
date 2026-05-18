import {
    Button,
    TextField,
    Select,
    MenuItem,
    FormControl,
} from "@mui/material";
import { MapPin, Search, Bell } from "lucide-react";

import { useLocation } from "../LocationContext";

const locations = [
    "Pune",
    "Mumbai",
    "Ahmedabad",
    "Coimbatore",
    "Hyderabad",
    "Bangalore Domlur office",
    "Bangalore Signet",
    "Chennai",
];

export function Navbar() {
    const { location, setLocation } = useLocation();

    return (

        <nav className="h-16 flex items-center justify-between px-8 border-b sticky top-0 z-30 
bg-[#020817] text-gray-200 border-gray-800">


            {/* LEFT */}
            <div className="flex items-center gap-6 flex-1">

                {/* Location */}
                <div className="flex items-center gap-2 min-w-[180px]">
                    <MapPin size={18} className="text-indigo-400" />

                    <FormControl size="small" fullWidth>
                        <Select
                            value={location}
                            onChange={(e) => setLocation(e.target.value)}
                            sx={{
                                color: "white",
                                borderRadius: "999px",
                                backgroundColor: "rgba(0,0,0,0.05)",
                            }}
                        >
                            {locations.map((loc) => (
                                <MenuItem key={loc} value={loc}>
                                    {loc}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </div>

                {/* Search */}
                <div className="relative w-full max-w-md hidden md:block">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <TextField
                        size="small"
                        placeholder="Search rooms..."
                        fullWidth
                        InputProps={{
                            style: {
                                paddingLeft: 36,
                                borderRadius: 999,
                                backgroundColor: "rgba(0,0,0,0.05)",
                                color: "white",
                            },
                        }}
                    />
                </div>
            </div>

            {/* RIGHT */}
            <div className="flex items-center gap-3">

                {/* Notification */}
                <Button sx={{ minWidth: 0, color: "white" }}>
                    <Bell size={18} />
                </Button>

            </div>
        </nav>
    );
}