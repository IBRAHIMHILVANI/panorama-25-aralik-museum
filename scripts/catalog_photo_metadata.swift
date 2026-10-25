import Foundation
import ImageIO
let base=URL(fileURLWithPath:CommandLine.arguments[1]);let files=try FileManager.default.contentsOfDirectory(at:base,includingPropertiesForKeys:nil).filter{$0.pathExtension.lowercased()=="heic"}.sorted{$0.lastPathComponent<$1.lastPathComponent}
var records:[[String:Any]]=[]
for u in files {
 guard let src=CGImageSourceCreateWithURL(u as CFURL,nil),let p=CGImageSourceCopyPropertiesAtIndex(src,0,nil) as? [String:Any] else {continue}
 let ex=p[kCGImagePropertyExifDictionary as String] as? [String:Any] ?? [:];let gps=p[kCGImagePropertyGPSDictionary as String] as? [String:Any] ?? [:];let tiff=p[kCGImagePropertyTIFFDictionary as String] as? [String:Any] ?? [:]
 var row:[String:Any]=["file":u.lastPathComponent,"exif":ex,"gps":gps,"tiff":tiff]
 for k in [kCGImagePropertyPixelWidth,kCGImagePropertyPixelHeight,kCGImagePropertyOrientation] {if let v=p[k as String]{row[k as String]=v}}
 records.append(row)
}
let data=try JSONSerialization.data(withJSONObject:records,options:[.prettyPrinted,.sortedKeys])
try data.write(to:URL(fileURLWithPath:CommandLine.arguments[2]))
let gpsCount=records.filter { !($0["gps"] as! [String:Any]).isEmpty }.count
print("Metadata records: \(records.count), GPS records: \(gpsCount)")
