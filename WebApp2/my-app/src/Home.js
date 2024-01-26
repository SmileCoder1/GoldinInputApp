import {useState, useEffect} from 'react';
import BlogList from './BlogList';


const Home = () => {


    //example code for creating button stuff
    // // let myName = "lolladin"
    // const [myName, setName] = useState('mario'); //the name of the variable and the function used to update that variables

    // const handleClick = (e) => {
    //     console.log('harro');
    // }

    // const handleClickAgain = (nameHere, e) =>
    // {
    //     setName(nameHere);
    // }


    // return ( 

    //     <div className="home">
    //         <h2>{myName}</h2>
    //         <button onClick={handleClick}>Click me</button>
    //         <button onClick={(e) => {
    //             handleClickAgain("mario " + Math.random() * 10, e);
    //             console.log(e);
    //         }}>Click here again</button>
    //     </div>
    //  );

    const [blogs, setBlogs] = useState([
        {title: "title1", body: "text1", author: "mario", id: 1},
        {title: "title2", body: "text2", author: "Yoshi", id: 2},
        {title: "title3", body: "text3", author: "kafka", id: 3}
    ]);

    const handleDelete = (id) => {
        const newBlogs = blogs.filter(blog => blog.id !== id);
        setBlogs(newBlogs);
    }


    const [dummyvar, setDummyvar] = useState("foo");
    
    


    return(
        <div className="home">
            <BlogList blogs={blogs} title = {dummyvar} handleDelete={handleDelete} />
            <BlogList blogs={blogs.filter((blog) => blog.author === 'mario')} title="Mario's blogs" handleDelete={handleDelete}/>
        </div>
    );

}
 
export default Home;