import Routes from "./routes"
import AuthProvider from "./provider/AuthProvider";
import 'bootstrap/dist/css/bootstrap.min.css';
function App() {
  return (
    <AuthProvider>
      <Routes />
    </AuthProvider>
  );
}

export default App;