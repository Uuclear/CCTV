/** 站点顶栏：品牌与主导航 */
import { Link } from "react-router-dom";

export default function SiteHeader() {
  return (
    <header className="site-header">
      <Link to="/" className="brand" aria-label="幕色首页">
        <span className="brand-mark">幕色</span>
        <span className="brand-sub">Muse Walls</span>
      </Link>
      <nav className="nav-links" aria-label="主导航">
        <Link to="/gallery">壁纸馆</Link>
        <Link to="/wish">许愿池</Link>
        <Link to="/categories">分类</Link>
        <Link to="/admin">管理</Link>
      </nav>
    </header>
  );
}
