import Navbar from './Navbar';
import Home from './Home';





function App() {
  const title = "Welcome to the new app";
  const likes = 50; 
  var randomNumber = Math.random() * 20;
  const link = "http://www.google.com";




  return (
    <div className="App">
      <Navbar />
      <div className="content">
      <Home />
      </div>
    </div>
  );
}

export default App;