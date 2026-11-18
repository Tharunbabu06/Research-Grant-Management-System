export default function UniversityBrand({ children }) {
  return (
    <div className="university-brand">
      {/* Official asset: https://www.kletech.ac.in/images/logo.png.
          Show its square emblem beside readable text on the white header. */}
      <span className="university-logo" aria-hidden="true">
        <img src="/kle-logo.png" alt="" />
      </span>
      <div className="university-name">
        {children || <>KLE Technological University,<span>Hubballi</span></>}
      </div>
    </div>
  );
}
