import React, {useRef, useState} from 'react'
import NavbarComponent from '../components/NavbarComponent'
import axios from "axios";

function Upload() {
  const fileInputRef=useRef();
  const [file,setFile] = useState();
  
  const handleChange = async (event) =>{
    setFile(event.target.files[0])
  }

  function handleSubmit(event) {
    event.preventDefault()
    const url = `${process.env.REACT_APP_BACKEND_URL}/upload_movies/`;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('fileName', file.name);
    const config = {
      headers: {
        'content-type': 'multipart/form-data',
      },
    };
    axios.post(url, formData, config).then((response) => {
      console.log(response.data);
    });

  }
  return(
    <div>
      <button onClick={()=>fileInputRef.current.click()}>
        Custom File Input Button
      </button>
      <input onChange={handleChange} multiple={false} ref={fileInputRef} type='file'hidden/>
      <button onClick={handleSubmit}>Submit</button>
    </div>

  )
}


export default Upload