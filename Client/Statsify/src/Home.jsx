import { useState } from "react";
import './Styles/Home.css'


// Now, when I click on the login to spotify button, I want to get the oauth
function Home() {
    const [userInfo, setUserInfo] = useState({})
    useEffect(() => {{
        fetch('http://localhost:5000/api/user-info')
            .then(response => response.json())
            .then(data => setUserInfo(data))
            .catch(error => console.error(error))
    }}, []);
    return (
        <>
            <h1 className="title">Welcome to Statsify!</h1>
            <h3>To view Spotify Statistics or gain listening insights, please login!</h3>
            <h1>User Info</h1>
            <p>Name: {userInfo.display_name}</p>
        </>
    )
}

export default Home