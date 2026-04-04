import { useState } from "react";

function Comment() {
  const [comment, setComment] = useState("");

  const handleSubmit = () => {
    console.log(comment);
    setComment("");
  };

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Add Comment</h3>

      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Write something..."
      />

      <br />

      <button onClick={handleSubmit}>
        Submit
      </button>
    </div>
  );
}

export default Comment;
