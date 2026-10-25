import Foundation
import Vision
import ImageIO

let url = URL(fileURLWithPath: CommandLine.arguments[1])
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
let image = CGImageSourceCreateImageAtIndex(source, 0, nil)!
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false
request.recognitionLanguages = ["tr-TR", "en-US"]
request.minimumTextHeight = 0.001
request.regionOfInterest = CGRect(x: 0.288, y: 0.426, width: 0.073, height: 0.214)
if CommandLine.arguments.count > 3 { request.regionOfInterest = CGRect(x: 0, y: 0, width: 1, height: 1) }
try VNImageRequestHandler(cgImage: image, orientation: .up, options: [:]).perform([request])
let rows: [[String: Any]] = (request.results ?? []).map { item in
    let box = item.boundingBox
    return ["text": item.topCandidates(1).first?.string ?? "", "confidence": item.topCandidates(1).first?.confidence ?? 0, "box": [box.origin.x, box.origin.y, box.width, box.height]]
}
let result: [String: Any] = ["source": url.lastPathComponent, "width": image.width, "height": image.height, "rows": rows]
let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
try data.write(to: URL(fileURLWithPath: CommandLine.arguments[2]))
print("Recognized \(rows.count) text lines from native \(image.width)x\(image.height) source")
